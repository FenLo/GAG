const { SlashCommandBuilder, PermissionFlagsBits } = require('discord.js');
const { logModerationAction } = require('../database');

module.exports = {
    data: new SlashCommandBuilder()
        .setName('ban')
        .setDescription('Bir kullanıcıyı sunucudan yasaklar.')
        .addUserOption(option =>
            option.setName('member')
                .setDescription('Yasaklanacak kullanıcı')
                .setRequired(true))
        .addStringOption(option =>
            option.setName('reason')
                .setDescription('Yasaklama sebebi')
                .setRequired(false))
        .setDefaultMemberPermissions(PermissionFlagsBits.Administrator),
    async execute(interaction) {
        await interaction.deferReply();

        const member = interaction.options.getMember('member');
        const reason = interaction.options.getString('reason') || 'Sebep belirtilmedi';

        if (!member) {
            return await interaction.followUp({ content: '❌ Kullanıcı bulunamadı.', ephemeral: true });
        }

        try {
            await member.ban({ reason });
            await interaction.followUp(`⛔ ${member.user.tag} adlı kullanıcı banlandı. Sebep: ${reason}`);
            
            logModerationAction(
                interaction.guild.id,
                interaction.guild.name,
                member.id,
                member.displayName,
                interaction.user.id,
                interaction.user.displayName,
                'ban',
                reason
            );
        } catch (error) {
            console.error('Ban error:', error);
            await interaction.followUp({ content: '❌ Bu kullanıcıyı banlamak için yetkim yok.', ephemeral: true });
        }
    }
};
