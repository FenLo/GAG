const { SlashCommandBuilder, PermissionFlagsBits } = require('discord.js');
const { logModerationAction } = require('../database');

module.exports = {
    data: new SlashCommandBuilder()
        .setName('kick')
        .setDescription('Bir kullanıcıyı sunucudan atar.')
        .addUserOption(option =>
            option.setName('member')
                .setDescription('Atılacak kullanıcı')
                .setRequired(true))
        .addStringOption(option =>
            option.setName('reason')
                .setDescription('Atma sebebi')
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
            await member.kick(reason);
            await interaction.followUp(`🚪 ${member.user.tag} adlı kullanıcı atıldı. Sebep: ${reason}`);
            
            logModerationAction(
                interaction.guild.id,
                interaction.guild.name,
                member.id,
                member.displayName,
                interaction.user.id,
                interaction.user.displayName,
                'kick',
                reason
            );
        } catch (error) {
            console.error('Kick error:', error);
            await interaction.followUp({ content: '❌ Bu kullanıcıyı atmak için yetkim yok.', ephemeral: true });
        }
    }
};
