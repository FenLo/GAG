const { SlashCommandBuilder, PermissionFlagsBits } = require('discord.js');
const { logModerationAction } = require('../database');

module.exports = {
    data: new SlashCommandBuilder()
        .setName('unmute')
        .setDescription('Bir kullanıcının susturmasını kaldırır.')
        .addUserOption(option =>
            option.setName('member')
                .setDescription('Susturması kaldırılacak kullanıcı')
                .setRequired(true))
        .setDefaultMemberPermissions(PermissionFlagsBits.Administrator),
    async execute(interaction) {
        await interaction.deferReply();

        const member = interaction.options.getMember('member');

        if (!member) {
            return await interaction.followUp({ content: '❌ Kullanıcı bulunamadı.', ephemeral: true });
        }

        try {
            await member.timeout(null);
            await interaction.followUp(`🔊 ${member} adlı kullanıcının susturması kaldırıldı.`);
            
            logModerationAction(
                interaction.guild.id,
                interaction.guild.name,
                member.id,
                member.displayName,
                interaction.user.id,
                interaction.user.displayName,
                'unmute',
                'Sebep belirtilmedi'
            );
        } catch (error) {
            console.error('Unmute error:', error);
            await interaction.followUp({ content: '❌ Bu kullanıcının susturmasını kaldırmak için yetkim yok.', ephemeral: true });
        }
    }
};
